## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.1128 | 0.48 | ❌ rejected |
| 8 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0107 | 0.35 | ❌ rejected |
| 7 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.0635 | 0.00 | ❌ rejected |
| 6 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.4735 | 0.82 | ❌ rejected |
| 5 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2073 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.48 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.113) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_high
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
    - 0.04
    - 0.08
    orientation:
      mode: none
  parameters:
    clearance_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_final
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
    - 0.04
    - 0.0
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_through
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.16
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
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
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.08]
  - orientation: mode=none
  - parameter_bindings:
    - clearance_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_final** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.113
- **task_score** (E): 0.483
- **fitness_score**: 0.423  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.560

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1272 |
| approach_descent | 1.00 | 1.00 | 0.1201 |
| contact_peg | 1.00 | 1.00 | 0.0397 |
| push_through | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.123, 0.202) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.528 | 2.179 |
| approach_descent | descend | 1.00 / step_budget | (0.495, 0.123, 0.202)→(0.496, 0.120, 0.083) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.540 | 0.618 |
| contact_peg | contact | 1.00 / force_exceeded | (0.496, 0.120, 0.083)→(0.495, 0.106, 0.046) | (0.500, 0.080, 0.034)→(0.500, 0.078, 0.036) | 0.161→0.158 | 1.00 / 2.000 | 8.474 | 8.474 |
| push_through | push | 0.00 / guard_failure | (0.494, 0.014, 0.037)→(0.494, 0.013, 0.037) | (0.500, 0.078, 0.036)→(0.505, -0.017, 0.039) | 0.158→0.064 | 1.00 / 3.000 | 9.376 | 55.433 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.834
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.834
- phase_score: 0.484
- phase_breakdown.push_score: 0.426
- phase_breakdown.contact_score: 0.731
- phase_breakdown.approach_score: 0.411

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.624
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.834
- **Median Q (composite search score)**: 0.038
- **K-run variance**: 0.0207
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.282


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26804,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_descent.speed":0.07143,"approach_high.arc_height":0.13714,"approach_high.clearance_height":0.15498,"approach_high.speed":0.03029,"contact_peg.contact_force":7.69282,"contact_peg.speed":0.03375,"push_through.force_threshold":59.7994,"push_through.push_distance":0.19858,"push_through.push_speed":0.09558,"push_through.push_tolerance":0.01253},"optimized_scores":{"best_composite_score":0.31424,"best_fitness_score":0.62424,"best_task_score":0.83426},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":631.0,"contact_point_centroid":[0.50226,0.00958,0.03847],"force_p95":53.4732,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.32989,"mean_force":35.66581,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49735,0.01965,0.04028]},{"body_a":"peg","body_b":"channel_base_body","contact_count":637.0,"contact_point_centroid":[0.50583,-0.01368,0.00979],"force_p95":43.00302,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.97915,"mean_force":29.9817,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49735,0.02028,0.04034]},{"body_a":"peg","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.50695,-0.10047,0.04901],"force_p95":35.98813,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.52852,"mean_force":30.41844,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49836,-0.03622,0.03692]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":404.0,"contact_point_centroid":[0.52514,-0.02465,0.0254],"force_p95":23.12766,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.41654,"mean_force":16.23262,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49777,-0.00281,0.03905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":232.0,"contact_point_centroid":[0.50433,0.05699,0.00944],"force_p95":3.39677,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.4171,"mean_force":0.85907,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49847,0.0943,0.06396]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50182,0.07789,0.05558],"force_p95":7.22296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.16895,"mean_force":4.50437,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49839,0.08972,0.05159]},{"body_a":"peg","body_b":"channel_base_body","contact_count":603.0,"contact_point_centroid":[0.50354,0.0616,0.00934],"force_p95":0.64158,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55971,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50465,0.13918,0.26878]},{"body_a":"peg","body_b":"channel_base_body","contact_count":382.0,"contact_point_centroid":[0.50385,0.06156,0.00936],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64281,"mean_force":0.54695,"phase_index":1.0,"phase_name":"approach_descent","phase_type":"descend","tcp_position_centroid":[0.50372,0.10029,0.14388]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49959,0.19868,0.29969]}],"total_contact_groups":9},"final_pose_error":0.10186,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50695,-0.0719,0.04014],"final_tcp_position":[0.49826,-0.03754,0.0366],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":63.32989,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":626.0,"n_steps_budget":1000.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.47071,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":622.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50846,0.10026,0.20447],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1751,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.50369,0.06158,0.03377],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14177,"object_z_max":0.03377,"peak_contact_force":0.52253,"phase_name":"approach_descent","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":382.0,"raw_peak_contact_force":0.64281,"subtask_id":"approach","tcp_end":[0.50073,0.10073,0.08323],"tcp_start":[0.50846,0.10026,0.20447],"tcp_to_object_dist_end":0.06315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":232.0,"n_steps_budget":990.0,"object_pos_end":[0.50381,0.05933,0.03595],"object_pos_start":[0.50369,0.06158,0.03377],"object_to_goal_dist_end":0.13944,"object_to_goal_dist_start":0.14177,"object_z_max":0.03596,"peak_contact_force":8.4171,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":250.0,"raw_peak_contact_force":8.4171,"subtask_id":"contact","tcp_end":[0.49861,0.08806,0.04712],"tcp_start":[0.50073,0.10073,0.08323],"tcp_to_object_dist_end":0.03126,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":637.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,-0.07191,0.04015],"object_pos_start":[0.50381,0.05933,0.03595],"object_to_goal_dist_end":0.0107,"object_to_goal_dist_start":0.13944,"object_z_max":0.04038,"peak_contact_force":0.0,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1697.0,"raw_peak_contact_force":63.32989,"subtask_id":"push","tcp_end":[0.49826,-0.03754,0.0366],"tcp_start":[0.49829,-0.03751,0.03665],"tcp_to_object_dist_end":0.03564,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87006,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_descent.speed":0.04555,"approach_high.arc_height":0.14601,"approach_high.clearance_height":0.16316,"approach_high.speed":0.04498,"contact_peg.contact_force":8.22877,"contact_peg.speed":0.02459,"push_through.force_threshold":38.64563,"push_through.push_distance":0.21198,"push_through.push_speed":0.06203,"push_through.push_tolerance":0.03076},"optimized_scores":{"best_composite_score":-0.01346,"best_fitness_score":0.29654,"best_task_score":0.32623},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":59.0,"contact_point_centroid":[0.49986,0.1078,0.04266],"force_p95":29.96854,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.75286,"mean_force":9.44301,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49453,0.11899,0.03964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":43.0,"contact_point_centroid":[0.50349,0.07535,0.00987],"force_p95":29.71473,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.67492,"mean_force":11.56006,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49465,0.11846,0.03972]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52524,0.07791,0.03302],"force_p95":18.99,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.8564,"mean_force":3.17991,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49427,0.10484,0.03818]},{"body_a":"peg","body_b":"channel_base_body","contact_count":266.0,"contact_point_centroid":[0.50151,0.11008,0.00954],"force_p95":6.29174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.63567,"mean_force":1.11122,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4952,0.14832,0.06185]},{"body_a":"attachment","body_b":"peg","contact_count":35.0,"contact_point_centroid":[0.49894,0.13123,0.05156],"force_p95":7.29128,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.38784,"mean_force":4.66735,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49551,0.14296,0.04813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":348.0,"contact_point_centroid":[0.50103,0.11608,0.00935],"force_p95":0.64605,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56748,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.4984,0.19101,0.24627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.50095,0.1159,0.00942],"force_p95":0.59667,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65734,"mean_force":0.54275,"phase_index":1.0,"phase_name":"approach_descent","phase_type":"descend","tcp_position_centroid":[0.49672,0.16052,0.14424]}],"total_contact_groups":7},"final_pose_error":0.18861,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50678,0.06161,0.03778],"final_tcp_position":[0.49428,0.0885,0.03703],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":42.75286,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11608,0.03392],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.56734,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":348.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49824,0.1654,0.20499],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,0.11609,0.03381],"object_pos_start":[0.50092,0.11608,0.03392],"object_to_goal_dist_end":0.19619,"object_to_goal_dist_start":0.19618,"object_z_max":0.03395,"peak_contact_force":0.54562,"phase_name":"approach_descent","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":411.0,"raw_peak_contact_force":0.65734,"subtask_id":"approach","tcp_end":[0.49709,0.15605,0.08304],"tcp_start":[0.49824,0.1654,0.20499],"tcp_to_object_dist_end":0.06353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":271.0,"n_steps_budget":1000.0,"object_pos_end":[0.50196,0.11203,0.03564],"object_pos_start":[0.50097,0.11609,0.03381],"object_to_goal_dist_end":0.19209,"object_to_goal_dist_start":0.19619,"object_z_max":0.03616,"peak_contact_force":8.63567,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":301.0,"raw_peak_contact_force":8.63567,"subtask_id":"contact","tcp_end":[0.49588,0.1409,0.04284],"tcp_start":[0.49709,0.15605,0.08304],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":93.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,0.06224,0.03759],"object_pos_start":[0.50196,0.11203,0.03564],"object_to_goal_dist_end":0.14243,"object_to_goal_dist_start":0.19209,"object_z_max":0.03839,"peak_contact_force":23.44633,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":142.0,"raw_peak_contact_force":42.75286,"subtask_id":"push","tcp_end":[0.49428,0.0885,0.03703],"tcp_start":[0.49428,0.08885,0.03709],"tcp_to_object_dist_end":0.0291,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85778,"average_solve_count":225.0,"average_success_count":225.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_descent.speed":0.07107,"approach_high.arc_height":0.16375,"approach_high.clearance_height":0.14858,"approach_high.speed":0.03569,"contact_peg.contact_force":8.34924,"contact_peg.speed":0.01313,"push_through.force_threshold":50.15357,"push_through.push_distance":0.19699,"push_through.push_speed":0.06554,"push_through.push_tolerance":0.02104},"optimized_scores":{"best_composite_score":0.03752,"best_fitness_score":0.34752,"best_task_score":0.28713},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":268.0,"contact_point_centroid":[0.49345,0.03058,0.03972],"force_p95":40.49783,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.21539,"mean_force":32.00043,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48862,0.04072,0.04165]},{"body_a":"peg","body_b":"channel_base_body","contact_count":264.0,"contact_point_centroid":[0.49761,0.00718,0.00989],"force_p95":40.0447,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.80414,"mean_force":32.16226,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48859,0.04227,0.04176]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52513,-0.02616,0.02343],"force_p95":25.36958,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.12592,"mean_force":17.48284,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48923,-0.00749,0.03836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.4962,0.05962,0.00948],"force_p95":4.47381,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.36954,"mean_force":0.84844,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48835,0.09655,0.06308]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.493,0.08018,0.05584],"force_p95":6.41267,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.08992,"mean_force":3.55513,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4889,0.09192,0.05116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":557.0,"contact_point_centroid":[0.49547,0.0638,0.00937],"force_p95":0.5815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56084,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48614,0.13986,0.26163]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49896,0.19771,0.29911]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.49489,0.06386,0.0094],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54538,"phase_index":1.0,"phase_name":"approach_descent","phase_type":"descend","tcp_position_centroid":[0.48297,0.10314,0.13988]}],"total_contact_groups":8},"final_pose_error":0.1246,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50237,-0.04062,0.04025],"final_tcp_position":[0.48911,-0.01085,0.03804],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":60.21539,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":584.0,"n_steps_budget":1000.0,"object_pos_end":[0.49525,0.06402,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14423,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54623,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":585.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.47837,0.10345,0.19803],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.49532,0.06372,0.03401],"object_pos_start":[0.49525,0.06402,0.03395],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14423,"object_z_max":0.03401,"peak_contact_force":0.55061,"phase_name":"approach_descent","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":401.0,"raw_peak_contact_force":0.55289,"subtask_id":"approach","tcp_end":[0.4899,0.10324,0.0822],"tcp_start":[0.47837,0.10345,0.19803],"tcp_to_object_dist_end":0.06257,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.49547,0.06172,0.03588],"object_pos_start":[0.49532,0.06372,0.03401],"object_to_goal_dist_end":0.14185,"object_to_goal_dist_start":0.14392,"object_z_max":0.03591,"peak_contact_force":8.36954,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":298.0,"raw_peak_contact_force":8.36954,"subtask_id":"contact","tcp_end":[0.48936,0.09024,0.04683],"tcp_start":[0.4899,0.10324,0.0822],"tcp_to_object_dist_end":0.03115,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.50242,-0.04021,0.04029],"object_pos_start":[0.49547,0.06172,0.03588],"object_to_goal_dist_end":0.03987,"object_to_goal_dist_start":0.14185,"object_z_max":0.04093,"peak_contact_force":4.68176,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":552.0,"raw_peak_contact_force":60.21539,"subtask_id":"push","tcp_end":[0.48911,-0.01085,0.03804],"tcp_start":[0.48915,-0.01068,0.03809],"tcp_to_object_dist_end":0.03231,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```