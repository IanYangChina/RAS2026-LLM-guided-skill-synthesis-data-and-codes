## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2437 | 0.83 | ✅ accepted |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.833, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.244) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.244
- **task_score** (E): 0.833
- **fitness_score**: 0.684  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2615 |
| approach_1 | 1.00 | 1.00 | 0.0099 |
| contact_1 | 1.00 | 1.00 | 0.0114 |
| push_1 | 0.33 | 1.00 | 0.1503 |
| retract_1 | 0.00 | 1.00 | 0.1182 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.051) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 111.931 | 119.907 |
| approach_1 | approach | 1.00 / step_budget | (0.495, 0.125, 0.051)→(0.496, 0.122, 0.042) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 39.219 | 141.478 |
| contact_1 | contact | 1.00 / step_budget | (0.496, 0.122, 0.042)→(0.497, 0.114, 0.036) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.333 | 141.578 | 159.378 |
| push_1 | push | 0.33 / step_budget | (0.497, 0.114, 0.036)→(0.498, -0.037, 0.037) | (0.500, 0.080, 0.034)→(0.500, -0.066, 0.036) | 0.160→0.018 | 1.00 / 2.333 | 63.936 | 124.226 |
| retract_1 | retract | 0.00 / step_budget | (0.498, -0.037, 0.037)→(0.496, 0.006, 0.147) | (0.500, -0.066, 0.036)→(0.500, -0.067, 0.034) | 0.018→0.018 | 1.00 / 1.333 | 1.116 | 64.472 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.884
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.884
- phase_score: 0.648
- phase_breakdown.approach_score: 0.856
- phase_breakdown.push_score: 0.564
- phase_breakdown.contact_score: 0.691

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.742
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.252
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.560


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51462,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00042,"approach_1.approach_height":0.18589,"contact_1.contact_force":18.55423,"push_1.push_distance":0.1317,"push_1.push_speed":0.09224,"retract_1.retract_height":0.05083,"retract_1.speed":0.08672},"optimized_scores":{"best_composite_score":0.30238,"best_fitness_score":0.74238,"best_task_score":0.88423},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.10482,0.06],"force_p95":116.55472,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.55472,"mean_force":116.55472,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50457,0.10474,0.04324]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":699.0,"contact_point_centroid":[0.54458,0.02801,0.05999],"force_p95":103.82187,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.46434,"mean_force":84.34857,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49983,0.03004,0.03668]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":327.0,"contact_point_centroid":[0.54556,0.0976,0.05997],"force_p95":113.6143,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.42509,"mean_force":77.26061,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50097,0.09694,0.03612]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":246.0,"contact_point_centroid":[0.52502,0.09709,0.05999],"force_p95":112.31273,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.94108,"mean_force":79.56813,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50103,0.09694,0.03618]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52502,0.09679,0.05999],"force_p95":64.50743,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.62336,"mean_force":22.59349,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50101,0.09665,0.03613]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54299,-0.04752,0.05999],"force_p95":62.41682,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.75801,"mean_force":59.34608,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49833,-0.05166,0.03672]},{"body_a":"attachment","body_b":"peg","contact_count":389.0,"contact_point_centroid":[0.50057,-0.00309,0.03942],"force_p95":17.16645,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.26916,"mean_force":3.53923,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4995,0.00858,0.03675]},{"body_a":"peg","body_b":"channel_base_body","contact_count":775.0,"contact_point_centroid":[0.49983,-0.01154,0.00967],"force_p95":14.51155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.47313,"mean_force":2.09813,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4998,0.02763,0.0367]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.50598,-0.10017,0.05966],"force_p95":20.61002,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.69417,"mean_force":14.07853,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49834,-0.05104,0.03673]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":192.0,"contact_point_centroid":[0.47479,0.00607,0.02812],"force_p95":2.19602,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.7501,"mean_force":0.74825,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50001,0.03523,0.03677]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.50523,-0.06242,0.05178],"force_p95":2.57971,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.32592,"mean_force":0.60378,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49745,-0.05059,0.03784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50603,-0.10027,0.05987],"force_p95":2.88306,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.29053,"mean_force":0.62358,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49795,-0.05153,0.03708]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":74.0,"contact_point_centroid":[0.52519,-0.05829,0.02565],"force_p95":2.73771,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.90405,"mean_force":0.60324,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49893,-0.02944,0.03681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":812.0,"contact_point_centroid":[0.50369,0.06161,0.00935],"force_p95":0.64051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55646,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50246,0.15146,0.16945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.50657,-0.07992,0.0094],"force_p95":0.55525,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79556,"mean_force":0.54788,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49534,-0.01868,0.10171]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49971,0.19912,0.29835]}],"total_contact_groups":18},"final_pose_error":0.12858,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50665,-0.07989,0.03383],"final_tcp_position":[0.49615,0.00255,0.17151],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":116.55472,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06154,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.5445,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":831.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50647,0.10562,0.04772],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":23.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.06161,0.03379],"object_pos_start":[0.50377,0.06154,0.03379],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14173,"object_z_max":0.03379,"peak_contact_force":116.55472,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":116.55472,"tcp_end":[0.50449,0.10469,0.043],"tcp_start":[0.50647,0.10562,0.04772],"tcp_to_object_dist_end":0.04406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":406.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.06157,0.0338],"object_pos_start":[0.50379,0.06161,0.03379],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14179,"object_z_max":0.0338,"peak_contact_force":114.42509,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":979.0,"raw_peak_contact_force":114.42509,"tcp_end":[0.50101,0.09668,0.03611],"tcp_start":[0.50449,0.10469,0.043],"tcp_to_object_dist_end":0.03529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50641,-0.08032,0.03664],"object_pos_start":[0.50379,0.06157,0.0338],"object_to_goal_dist_end":0.00724,"object_to_goal_dist_start":0.14176,"object_z_max":0.03737,"peak_contact_force":1.41421,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2144.0,"raw_peak_contact_force":114.46434,"tcp_end":[0.49833,-0.05161,0.03672],"tcp_start":[0.50101,0.09668,0.03611],"tcp_to_object_dist_end":0.02982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50665,-0.07989,0.03383],"object_pos_start":[0.50641,-0.08032,0.03664],"object_to_goal_dist_end":0.00907,"object_to_goal_dist_start":0.00724,"object_z_max":0.03665,"peak_contact_force":0.55412,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1022.0,"raw_peak_contact_force":62.75801,"tcp_end":[0.49615,0.00255,0.17151],"tcp_start":[0.49833,-0.05161,0.03672],"tcp_to_object_dist_end":0.16082,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28324,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00247,"approach_1.approach_height":0.16904,"contact_1.contact_force":7.45584,"push_1.push_distance":0.19488,"push_1.push_speed":0.09699,"retract_1.retract_height":0.16274,"retract_1.speed":0.05073},"optimized_scores":{"best_composite_score":0.25224,"best_fitness_score":0.69224,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":758.0,"contact_point_centroid":[0.54359,0.06993,0.05998],"force_p95":120.80291,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.93212,"mean_force":102.08052,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4979,0.07406,0.03632]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":283.0,"contact_point_centroid":[0.54773,0.12,0.05998],"force_p95":128.3165,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.33072,"mean_force":80.04581,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49551,0.14659,0.0343]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54344,-0.01537,0.06],"force_p95":74.34741,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.26816,"mean_force":57.06069,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49871,-0.01047,0.03693]},{"body_a":"peg","body_b":"channel_base_body","contact_count":715.0,"contact_point_centroid":[0.50395,0.02986,0.00968],"force_p95":21.93034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.17385,"mean_force":3.48011,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49791,0.07301,0.03631]},{"body_a":"attachment","body_b":"peg","contact_count":496.0,"contact_point_centroid":[0.50322,0.05992,0.04324],"force_p95":25.59705,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.03227,"mean_force":4.71749,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49798,0.07149,0.03641]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50076,0.11464,0.00945],"force_p95":0.65217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.27037,"mean_force":0.63327,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49521,0.1481,0.0352]},{"body_a":"attachment","body_b":"peg","contact_count":46.0,"contact_point_centroid":[0.50067,0.13372,0.04272],"force_p95":2.79028,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.98287,"mean_force":1.04541,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49668,0.14564,0.03421]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":375.0,"contact_point_centroid":[0.52521,0.04592,0.02967],"force_p95":6.31259,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.66259,"mean_force":1.38742,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.498,0.07492,0.03655]},{"body_a":"peg","body_b":"channel_base_body","contact_count":755.0,"contact_point_centroid":[0.50092,0.11599,0.00939],"force_p95":0.61661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55392,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4977,0.17803,0.1717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50185,-0.04446,0.00946],"force_p95":0.56055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.0191,"mean_force":0.5433,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49538,0.00681,0.08245]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50075,0.11655,0.00946],"force_p95":0.5787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58479,"mean_force":0.54094,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49639,0.15694,0.04619]}],"total_contact_groups":11},"final_pose_error":0.17152,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50113,-0.04437,0.03439],"final_tcp_position":[0.49582,0.01788,0.12946],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":136.93212,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11605,0.03394],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54801,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":755.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49706,0.15726,0.04892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11601,0.03391],"object_pos_start":[0.50095,0.11605,0.03394],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19615,"object_z_max":0.03394,"peak_contact_force":0.54838,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.58479,"tcp_end":[0.49634,0.15677,0.04264],"tcp_start":[0.49706,0.15726,0.04892],"tcp_to_object_dist_end":0.04193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.50145,0.11511,0.03456],"object_pos_start":[0.50092,0.11601,0.03391],"object_to_goal_dist_end":0.1952,"object_to_goal_dist_start":0.19611,"object_z_max":0.03456,"peak_contact_force":103.05412,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":747.0,"raw_peak_contact_force":131.33072,"tcp_end":[0.49714,0.14524,0.03415],"tcp_start":[0.49634,0.15677,0.04264],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50187,-0.04072,0.0362],"object_pos_start":[0.50145,0.11511,0.03456],"object_to_goal_dist_end":0.0395,"object_to_goal_dist_start":0.1952,"object_z_max":0.03829,"peak_contact_force":97.09645,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2344.0,"raw_peak_contact_force":136.93212,"tcp_end":[0.49874,-0.01032,0.03693],"tcp_start":[0.49714,0.14524,0.03415],"tcp_to_object_dist_end":0.03057,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50113,-0.04437,0.03439],"object_pos_start":[0.50187,-0.04072,0.0362],"object_to_goal_dist_end":0.03608,"object_to_goal_dist_start":0.0395,"object_z_max":0.0362,"peak_contact_force":0.54507,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":999.0,"raw_peak_contact_force":76.26816,"tcp_end":[0.49582,0.01788,0.12946],"tcp_start":[0.49874,-0.01032,0.03693],"tcp_to_object_dist_end":0.11376,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51163,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00148,"approach_1.approach_height":0.27896,"contact_1.contact_force":14.15289,"push_1.push_distance":0.17284,"push_1.push_speed":0.09073,"retract_1.retract_height":0.16827,"retract_1.speed":0.0659},"optimized_scores":{"best_composite_score":0.17643,"best_fitness_score":0.61643,"best_task_score":0.61387},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4749,0.12,0.0598],"force_p95":341.5277,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.62701,"mean_force":311.80708,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47984,0.111,0.05723]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47497,0.11792,0.05994],"force_p95":283.70214,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.29523,"mean_force":209.67753,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48303,0.11067,0.05591]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":409.0,"contact_point_centroid":[0.535,0.10349,0.05995],"force_p95":214.24986,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.3783,"mean_force":173.94326,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48947,0.10213,0.03793]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":751.0,"contact_point_centroid":[0.54077,0.0292,0.05999],"force_p95":113.24171,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":121.28051,"mean_force":95.35014,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49541,0.03122,0.03788]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5428,-0.04328,0.06],"force_p95":54.3664,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.39097,"mean_force":54.14531,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49775,-0.0477,0.03754]},{"body_a":"attachment","body_b":"peg","contact_count":320.0,"contact_point_centroid":[0.49691,0.01212,0.0398],"force_p95":11.79927,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.98114,"mean_force":2.51414,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49565,0.02386,0.03788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":803.0,"contact_point_centroid":[0.49825,-0.00835,0.00961],"force_p95":5.08578,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.45117,"mean_force":1.43328,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49545,0.03015,0.03788]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52516,0.01218,0.05876],"force_p95":10.05679,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.54612,"mean_force":5.50063,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49519,0.04195,0.03805]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":157.0,"contact_point_centroid":[0.4748,-0.02158,0.03149],"force_p95":1.07419,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.51931,"mean_force":0.53673,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49617,0.00981,0.03789]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.49531,0.0638,0.00938],"force_p95":0.56258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55591,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48773,0.15105,0.1656]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49933,0.19869,0.29695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.4937,-0.07645,0.00941],"force_p95":0.57267,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68345,"mean_force":0.54136,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49468,-0.02072,0.08736]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.49515,0.0639,0.0094],"force_p95":0.55087,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54517,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4894,0.10228,0.03802]},{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.49536,0.06392,0.0094],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54534,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48551,0.10908,0.05114]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":285.0,"contact_point_centroid":[0.47497,-0.07609,0.05432],"force_p95":0.27834,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.35163,"mean_force":0.05138,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49483,-0.02345,0.08199]}],"total_contact_groups":15},"final_pose_error":0.15981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49302,-0.07615,0.03378],"final_tcp_position":[0.49534,-0.00177,0.14027],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":355.62701,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49535,0.06392,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":334.70153,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":908.0,"raw_peak_contact_force":355.62701,"tcp_end":[0.481,0.11081,0.05671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":95.0,"n_steps_budget":600.0,"object_pos_end":[0.49532,0.06402,0.034],"object_pos_start":[0.49535,0.06392,0.03399],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14412,"object_z_max":0.034,"peak_contact_force":0.55289,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":125.0,"raw_peak_contact_force":307.29523,"tcp_end":[0.48856,0.10593,0.04095],"tcp_start":[0.481,0.11081,0.05671],"tcp_to_object_dist_end":0.04301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.49527,0.06412,0.03403],"object_pos_start":[0.49532,0.06402,0.034],"object_to_goal_dist_end":0.14432,"object_to_goal_dist_start":0.14422,"object_z_max":0.03403,"peak_contact_force":207.25489,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":848.0,"raw_peak_contact_force":232.3783,"tcp_end":[0.49312,0.0992,0.03757],"tcp_start":[0.48856,0.10593,0.04095],"tcp_to_object_dist_end":0.03533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49312,-0.07729,0.03559],"object_pos_start":[0.49527,0.06412,0.03403],"object_to_goal_dist_end":0.00861,"object_to_goal_dist_start":0.14432,"object_z_max":0.03975,"peak_contact_force":93.29657,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2040.0,"raw_peak_contact_force":121.28051,"tcp_end":[0.49776,-0.0476,0.03754],"tcp_start":[0.49312,0.0992,0.03757],"tcp_to_object_dist_end":0.03012,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49302,-0.07615,0.03378],"object_pos_start":[0.49312,-0.07729,0.03559],"object_to_goal_dist_end":0.01011,"object_to_goal_dist_start":0.00861,"object_z_max":0.03585,"peak_contact_force":2.24781,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1287.0,"raw_peak_contact_force":54.39097,"tcp_end":[0.49534,-0.00177,0.14027],"tcp_start":[0.49776,-0.0476,0.03754],"tcp_to_object_dist_end":0.12991,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```