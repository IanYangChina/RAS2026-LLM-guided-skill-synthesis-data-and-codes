## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push → lift | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5  | -0.0828 | 0.00 | ❌ rejected |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5  | -0.0805 | 0.00 | ✅ accepted |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5  | 0.3304 | 0.63 | ✅ accepted |

**Proposal policy**: task_score is 0.63 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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
| `object` | offset from object initial position (0.5030531481177555, 0.06746166958506708, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.09253833041493292, 0.04) | final destination targets |
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

## Current Skill (Q=0.330) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: push_progress
  target_entity: object
  metric: goal_progress
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: descend_to_peg
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.01
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_force_limit:
      type: scalar
      range:
      - 20.0
      - 39.0
      default: 35.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_established
    when: before_phase
    predicate: contact_detected
    args:
      body_a: attachment
      body_b: peg
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_progress
- id: lift_away
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
    offset:
    - 0.0
    - 0.0
    - 0.0

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]
- **descend_to_peg** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.01], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_force_limit: status=consumed; consumers=termination.force_threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_established, when=before_phase, predicate=contact_detected, on_failure=retry, threshold=1.0, args={'body_a': 'attachment', 'body_b': 'peg'}
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **lift_away** (`lift`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.330
- **task_score** (E): 0.635
- **fitness_score**: 0.529  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2423 |
| descend_to_peg | 1.00 | 1.00 | 0.0245 |
| push_channel | 1.00 | 1.00 | 0.0659 |
| lift_away | 1.00 | 1.00 | 0.1587 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.132, 0.069) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.542 | 2.127 |
| descend_to_peg | descend | 1.00 / step_budget | (0.496, 0.132, 0.069)→(0.497, 0.129, 0.045) | (0.501, 0.100, 0.034)→(0.501, 0.099, 0.034) | 0.180→0.179 | 1.00 / 1.000 | 0.530 | 1.686 |
| push_channel | push | 1.00 / force_exceeded | (0.497, 0.129, 0.045)→(0.494, 0.064, 0.039) | (0.501, 0.099, 0.034)→(0.507, 0.033, 0.039) | 0.179→0.114 | 1.00 / 3.000 | 31.826 | 25.845 |
| lift_away | lift | 1.00 / step_budget | (0.494, 0.064, 0.039)→(0.496, -0.067, 0.126) | (0.507, 0.033, 0.039)→(0.501, 0.001, 0.024) | 0.114→0.084 | 1.00 / 1.000 | 0.665 | 34.174 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.680
- alignment_error: None
- force_efficiency: 0.047
- terminal_score: 0.622
- phase_score: 0.453
- phase_breakdown.push_progress_score: 0.453

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.647
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.709
- **Median Q (composite search score)**: 0.337
- **K-run variance**: 0.0119
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.322


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.06667,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.01884,"descend_to_peg.descend_speed":0.04099,"lift_away.lift_speed":0.08566,"push_channel.push_force_limit":37.5903,"push_channel.push_speed":0.05325},"optimized_scores":{"best_composite_score":0.33709,"best_fitness_score":0.64709,"best_task_score":0.70853},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50108,-0.00024,0.04001],"force_p95":9.23032,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.06566,"mean_force":3.33766,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49485,0.00959,0.04081]},{"body_a":"attachment","body_b":"peg","contact_count":947.0,"contact_point_centroid":[0.50067,0.04164,0.04012],"force_p95":29.68711,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.48507,"mean_force":16.78301,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49515,0.05194,0.0402]},{"body_a":"peg","body_b":"channel_base_body","contact_count":331.0,"contact_point_centroid":[0.5058,-0.04249,0.00825],"force_p95":1.1315,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.38736,"mean_force":0.84001,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49478,-0.0303,0.08153]},{"body_a":"peg","body_b":"channel_base_body","contact_count":972.0,"contact_point_centroid":[0.50739,0.01811,0.00984],"force_p95":23.78475,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.70762,"mean_force":13.03765,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49521,0.0532,0.04032]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":885.0,"contact_point_centroid":[0.52523,0.02586,0.02775],"force_p95":15.00938,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.40044,"mean_force":9.06298,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4951,0.04919,0.04007]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52516,-0.00725,0.02235],"force_p95":10.33629,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.57923,"mean_force":4.27767,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49522,0.0081,0.04241]},{"body_a":"peg","body_b":"channel_base_body","contact_count":840.0,"contact_point_centroid":[0.50307,0.06749,0.00935],"force_p95":0.55314,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55689,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49879,0.15013,0.18077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":144.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49811,0.0999,0.05614]}],"total_contact_groups":8},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50487,-0.0459,0.02405],"final_tcp_position":[0.4964,-0.06932,0.12385],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":38.06566,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54559,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":840.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49937,0.10217,0.06797],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":144.0,"n_steps_budget":600.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54571,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":144.0,"raw_peak_contact_force":0.55077,"tcp_end":[0.49847,0.09795,0.04557],"tcp_start":[0.49937,0.10217,0.06797],"tcp_to_object_dist_end":0.03304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50754,-0.02236,0.03988],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.05813,"object_to_goal_dist_start":0.14759,"object_z_max":0.04037,"peak_contact_force":29.90287,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2804.0,"raw_peak_contact_force":33.48507,"subtask_id":"push_progress","tcp_end":[0.49562,0.01145,0.0394],"tcp_start":[0.49847,0.09795,0.04557],"tcp_to_object_dist_end":0.03586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":341.0,"n_steps_budget":990.0,"object_pos_end":[0.50487,-0.0459,0.02405],"object_pos_start":[0.50754,-0.02236,0.03988],"object_to_goal_dist_end":0.03796,"object_to_goal_dist_start":0.05813,"object_z_max":0.04039,"peak_contact_force":0.77007,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":362.0,"raw_peak_contact_force":38.06566,"tcp_end":[0.4964,-0.06932,0.12385],"tcp_start":[0.49562,0.01145,0.0394],"tcp_to_object_dist_end":0.10286,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22778,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.08518,"descend_to_peg.descend_speed":0.09443,"lift_away.lift_speed":0.05098,"push_channel.push_force_limit":35.74229,"push_channel.push_speed":0.06065},"optimized_scores":{"best_composite_score":0.46063,"best_fitness_score":0.52063,"best_task_score":0.62228},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.50249,0.0443,0.04209],"force_p95":15.42179,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.66982,"mean_force":8.00474,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49669,0.05438,0.0427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":446.0,"contact_point_centroid":[0.50471,0.00607,0.00826],"force_p95":6.5372,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.37727,"mean_force":1.38379,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.4959,-0.00464,0.08203]},{"body_a":"attachment","body_b":"peg","contact_count":838.0,"contact_point_centroid":[0.50163,0.0876,0.04152],"force_p95":31.56043,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.26213,"mean_force":14.05819,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49763,0.09858,0.04199]},{"body_a":"peg","body_b":"channel_base_body","contact_count":856.0,"contact_point_centroid":[0.50548,0.06414,0.00985],"force_p95":27.61653,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.54793,"mean_force":12.91568,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49768,0.09946,0.04209]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52512,0.04064,0.02274],"force_p95":11.0776,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.14563,"mean_force":6.07659,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49738,0.05228,0.04459]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":320.0,"contact_point_centroid":[0.52511,0.05038,0.0292],"force_p95":12.04397,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.00942,"mean_force":8.14911,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49761,0.07385,0.041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":719.0,"contact_point_centroid":[0.50358,0.11165,0.00938],"force_p95":0.61658,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55518,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5022,0.17117,0.18059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.50384,0.11136,0.0094],"force_p95":0.60089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62569,"mean_force":0.55916,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50299,0.14271,0.05836]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50309,0.12971,0.05884],"force_p95":1.12004,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.19974,"mean_force":0.63923,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50118,0.14172,0.04882]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4998,0.19941,0.29892]}],"total_contact_groups":10},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50323,0.00297,0.02409],"final_tcp_position":[0.4968,-0.06649,0.12584],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":47.66982,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":741.0,"n_steps_budget":1000.0,"object_pos_end":[0.5037,0.11179,0.03387],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19193,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54507,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":735.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50588,0.1441,0.0687],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":108.0,"n_steps_budget":600.0,"object_pos_end":[0.50374,0.1116,0.03382],"object_pos_start":[0.5037,0.11179,0.03387],"object_to_goal_dist_end":0.19173,"object_to_goal_dist_start":0.19193,"object_z_max":0.03387,"peak_contact_force":0.60194,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":111.0,"raw_peak_contact_force":1.62569,"tcp_end":[0.50108,0.14164,0.04808],"tcp_start":[0.50588,0.1441,0.0687],"tcp_to_object_dist_end":0.03337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.50736,0.02465,0.03954],"object_pos_start":[0.50374,0.1116,0.03382],"object_to_goal_dist_end":0.10491,"object_to_goal_dist_start":0.19173,"object_z_max":0.04053,"peak_contact_force":36.26213,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2014.0,"raw_peak_contact_force":36.26213,"subtask_id":"push_progress","tcp_end":[0.49779,0.05884,0.04062],"tcp_start":[0.50108,0.14164,0.04808],"tcp_to_object_dist_end":0.03553,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":451.0,"n_steps_budget":1000.0,"object_pos_end":[0.50323,0.00297,0.02409],"object_pos_start":[0.50736,0.02465,0.03954],"object_to_goal_dist_end":0.08455,"object_to_goal_dist_start":0.10491,"object_z_max":0.03959,"peak_contact_force":0.72552,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":496.0,"raw_peak_contact_force":47.66982,"tcp_end":[0.4968,-0.06649,0.12584],"tcp_start":[0.49779,0.05884,0.04062],"tcp_to_object_dist_end":0.12337,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12329,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.0624,"descend_to_peg.descend_speed":0.05193,"lift_away.lift_speed":0.04336,"push_channel.push_force_limit":27.58046,"push_channel.push_speed":0.05277},"optimized_scores":{"best_composite_score":0.19361,"best_fitness_score":0.42028,"best_task_score":0.5731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":119.0,"contact_point_centroid":[0.496,0.09322,0.04373],"force_p95":15.33075,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.78564,"mean_force":6.58607,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.48732,0.10143,0.04367]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":146.0,"contact_point_centroid":[0.52521,0.08299,0.0289],"force_p95":12.28888,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.26412,"mean_force":4.9564,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.48734,0.09446,0.04672]},{"body_a":"peg","body_b":"channel_base_body","contact_count":557.0,"contact_point_centroid":[0.49976,0.05543,0.00859],"force_p95":11.07987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.5522,"mean_force":1.85166,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49113,0.0227,0.08284]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47498,0.02335,0.02429],"force_p95":8.7159,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81793,"mean_force":2.75097,"phase_index":3.0,"phase_name":"lift_away","phase_type":"lift","tcp_position_centroid":[0.49303,-0.01217,0.10053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":237.0,"contact_point_centroid":[0.50293,0.09117,0.00991],"force_p95":5.12306,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.78919,"mean_force":2.46484,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48867,0.13453,0.03705]},{"body_a":"attachment","body_b":"peg","contact_count":194.0,"contact_point_centroid":[0.49464,0.12259,0.04826],"force_p95":4.99606,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.38693,"mean_force":2.47586,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48859,0.13367,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.49631,0.11548,0.00948],"force_p95":1.1814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.88168,"mean_force":0.62839,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48687,0.14921,0.05158]},{"body_a":"attachment","body_b":"peg","contact_count":76.0,"contact_point_centroid":[0.49313,0.137,0.05904],"force_p95":1.97205,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.37875,"mean_force":0.62662,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48916,0.14882,0.04555]},{"body_a":"peg","body_b":"channel_base_body","contact_count":728.0,"contact_point_centroid":[0.4962,0.11913,0.00942],"force_p95":0.61544,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55192,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49078,0.17452,0.18045]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49953,0.19923,0.29786]}],"total_contact_groups":10},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49424,0.04741,0.02409],"final_tcp_position":[0.49618,-0.06478,0.12762],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":29.31221,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11956,0.03383],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19969,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53622,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":752.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48356,0.1509,0.06925],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":600.0,"object_pos_end":[0.49606,0.11865,0.03475],"object_pos_start":[0.49608,0.11956,0.03383],"object_to_goal_dist_end":0.19876,"object_to_goal_dist_start":0.19969,"object_z_max":0.03475,"peak_contact_force":0.44116,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":477.0,"raw_peak_contact_force":2.88168,"tcp_end":[0.49125,0.1486,0.04108],"tcp_start":[0.48356,0.1509,0.06925],"tcp_to_object_dist_end":0.03098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.50645,0.09734,0.03635],"object_pos_start":[0.49606,0.11865,0.03475],"object_to_goal_dist_end":0.17749,"object_to_goal_dist_start":0.19876,"object_z_max":0.03652,"peak_contact_force":29.31221,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":431.0,"raw_peak_contact_force":7.78919,"subtask_id":"push_progress","tcp_end":[0.48859,0.12157,0.03617],"tcp_start":[0.49125,0.1486,0.04108],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":602.0,"n_steps_budget":1000.0,"object_pos_end":[0.49424,0.04741,0.02409],"object_pos_start":[0.50645,0.09734,0.03635],"object_to_goal_dist_end":0.12853,"object_to_goal_dist_start":0.17749,"object_z_max":0.04082,"peak_contact_force":0.49887,"phase_name":"lift_away","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":829.0,"raw_peak_contact_force":16.78564,"tcp_end":[0.49618,-0.06478,0.12762],"tcp_start":[0.48859,0.12157,0.03617],"tcp_to_object_dist_end":0.15268,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```