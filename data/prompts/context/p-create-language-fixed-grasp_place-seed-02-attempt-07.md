## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4051 | 0.95 | ❌ rejected |
| 6 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4079 | 0.95 | ❌ rejected |
| 5 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.3704 | 0.91 | ❌ rejected |
| 4 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.4338 | 1.00 | ✅ accepted |
| 3 | approach → descend → grasp → approach → descend | linear_cartesian | linear_cartesian | — | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | 9 | 0.3008 | 0.75 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach_1 | object | (0.00, 0.00, 0.00) | distance | approach_height |
| descend_1 | object | (0.00, 0.00, 0.02) | distance | grasp_z_offset |
| grasp_1 | object | (0.00, 0.00, 0.02) | contact | — |
| transport_arc | goal | (0.00, 0.00, 0.00) | distance | — |
| release_1 | goal | (0.00, 0.00, 0.00) | distance | — |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.405) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
phases:
- id: approach
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
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
  subtask_id: approach_1
- id: descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    grasp_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: descend_1
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: grasp_1
- id: transport
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
    transport_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: transport_arc
- id: place_descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.03
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    placement_z_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.03
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: release_1

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - grasp_z_offset: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)
    - transport_speed: status=consumed; consumers=generator.speed (replace)
- **place_descend** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.03], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - placement_z_offset: status=consumed; consumers=target.offset.z (replace)

## Design Metrics

- **Composite score**: 0.405
- **task_score** (E): 0.947
- **fitness_score**: 0.945  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1817 |
| descend | 1.00 | 1.00 | 0.0771 |
| grasp | 1.00 | 1.00 | 0.0115 |
| transport | 1.00 | 1.00 | 0.2630 |
| place_descend | 1.00 | 1.00 | 0.0298 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, -0.014, 0.124) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend | descend | 1.00 / step_budget | (0.490, -0.014, 0.124)→(0.488, -0.015, 0.046) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.488, -0.015, 0.046)→(0.480, -0.015, 0.038) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 44.333 | 0.135 | 0.175 |
| transport | approach | 1.00 / step_budget | (0.480, -0.015, 0.038)→(0.614, 0.150, 0.189) | (0.493, -0.015, 0.026)→(0.623, 0.150, 0.167) | 0.281→0.034 | 1.00 / 30.667 | 0.098 | 0.480 |
| place_descend | descend | 1.00 / step_budget | (0.614, 0.150, 0.189)→(0.632, 0.173, 0.184) | (0.623, 0.150, 0.167)→(0.636, 0.173, 0.156) | 0.034→0.012 | 1.00 / 23.333 | 0.129 | 0.254 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.744
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.630
- phase_breakdown.transport_arc_score: 0.517
- phase_breakdown.approach_1_score: 0.233
- phase_breakdown.release_1_score: 0.672
- phase_breakdown.descend_1_score: 0.837
- phase_breakdown.grasp_1_score: 1.000
- grasp_place_fitness: 0.974

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.974
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.434
- **K-run variance**: 0.0016
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: descend.grasp_z_offset
- **Final σ (mean)**: 0.423


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90941,"average_solve_count":287.0,"average_success_count":287.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.09587,"approach.speed":0.0262,"descend.grasp_z_offset":0.0159,"descend.speed":0.06691,"place_descend.place_speed":0.05044,"place_descend.placement_z_offset":0.01358,"transport.arc_height":0.05025,"transport.placement_z_offset":0.01335,"transport.transport_speed":0.0309},"optimized_scores":{"best_composite_score":0.34808,"best_fitness_score":0.88808,"best_task_score":0.84141},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":90.0,"contact_point_centroid":[0.47446,-0.01873,-0.00137],"force_p95":0.3504,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41649,"mean_force":0.13899,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.46334,-0.01909,0.04409]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":20770.0,"contact_point_centroid":[0.52576,0.02986,0.14314],"force_p95":0.07305,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25492,"mean_force":0.04927,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52494,0.04892,0.14114]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18180.0,"contact_point_centroid":[0.52486,0.06693,0.14232],"force_p95":0.07963,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24433,"mean_force":0.05523,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52386,0.04777,0.13991]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":13921.0,"contact_point_centroid":[0.62135,0.1688,0.19076],"force_p95":0.08918,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2276,"mean_force":0.06649,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61881,0.14985,0.19135]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16117.0,"contact_point_centroid":[0.62105,0.13111,0.19106],"force_p95":0.07992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21466,"mean_force":0.05669,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.61886,0.14989,0.19137]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47616,-0.02008,-0.00205],"force_p95":0.13647,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17635,"mean_force":0.12639,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46502,-0.01963,0.04403]},{"body_a":"world","body_b":"grasp_target","contact_count":2188.0,"contact_point_centroid":[0.47616,-0.02015,-0.00193],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48638,-0.00894,0.218]},{"body_a":"world","body_b":"grasp_target","contact_count":1148.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47174,-0.01903,0.0928]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5080.0,"contact_point_centroid":[0.46366,-0.00035,0.04565],"force_p95":0.06588,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09885,"mean_force":0.04293,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46392,-0.0196,0.04293]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5389.0,"contact_point_centroid":[0.46353,-0.03885,0.04515],"force_p95":0.06495,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0827,"mean_force":0.04113,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46393,-0.0196,0.04293]}],"total_contact_groups":10},"final_pose_error":0.01057,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63053,0.15711,0.16421],"final_tcp_position":[0.62687,0.15735,0.19424],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.41649,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.47434,-0.01837,0.13536],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.4716,-0.01978,0.05073],"tcp_start":[0.47434,-0.01837,0.13536],"tcp_to_object_dist_end":0.02513,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":47.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47608,-0.01973,0.02582],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28828,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.13487,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12269.0,"raw_peak_contact_force":0.17635,"subtask_id":"grasp_1","tcp_end":[0.4639,-0.0196,0.0429],"tcp_start":[0.4716,-0.01978,0.05073],"tcp_to_object_dist_end":0.02098,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61994,0.14201,0.17092],"object_pos_start":[0.47608,-0.01973,0.02582],"object_to_goal_dist_end":0.02814,"object_to_goal_dist_start":0.28828,"object_z_max":0.17102,"peak_contact_force":0.09413,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":39040.0,"raw_peak_contact_force":0.41649,"subtask_id":"transport_arc","tcp_end":[0.61295,0.14206,0.19547],"tcp_start":[0.4639,-0.0196,0.0429],"tcp_to_object_dist_end":0.02552,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.63053,0.15711,0.16421],"object_pos_start":[0.61994,0.14201,0.17092],"object_to_goal_dist_end":0.0259,"object_to_goal_dist_start":0.02814,"object_z_max":0.17092,"peak_contact_force":0.12461,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30038.0,"raw_peak_contact_force":0.2276,"subtask_id":"release_1","tcp_end":[0.62687,0.15735,0.19424],"tcp_start":[0.61295,0.14206,0.19547],"tcp_to_object_dist_end":0.03025,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7134,"average_solve_count":321.0,"average_success_count":321.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.09314,"approach.speed":0.05341,"descend.grasp_z_offset":0.01014,"descend.speed":0.01056,"place_descend.place_speed":0.09829,"place_descend.placement_z_offset":0.04302,"transport.arc_height":0.07366,"transport.placement_z_offset":0.03982,"transport.transport_speed":0.03597},"optimized_scores":{"best_composite_score":0.43351,"best_fitness_score":0.97351,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":85.0,"contact_point_centroid":[0.45703,-0.02448,-0.00137],"force_p95":0.40008,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.47231,"mean_force":0.16694,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.44618,-0.02499,0.03906]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10935.0,"contact_point_centroid":[0.61522,0.20654,0.15249],"force_p95":0.13572,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32917,"mean_force":0.08373,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.6099,0.18792,0.15195]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":12373.0,"contact_point_centroid":[0.61494,0.1692,0.15253],"force_p95":0.10758,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.28978,"mean_force":0.07436,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.60961,0.18756,0.1521]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":17787.0,"contact_point_centroid":[0.50492,0.03148,0.12704],"force_p95":0.08992,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26181,"mean_force":0.05789,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50299,0.05022,0.12587]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15245.0,"contact_point_centroid":[0.50367,0.06751,0.12616],"force_p95":0.10686,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24855,"mean_force":0.06613,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.50163,0.04849,0.12442]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45857,-0.02621,-0.00206],"force_p95":0.14133,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19212,"mean_force":0.1276,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44786,-0.02561,0.03887]},{"body_a":"world","body_b":"grasp_target","contact_count":2204.0,"contact_point_centroid":[0.45856,-0.02632,-0.00194],"force_p95":0.13205,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12285,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47857,-0.01173,0.21652]},{"body_a":"world","body_b":"grasp_target","contact_count":1348.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.45489,-0.02485,0.08921]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4828.0,"contact_point_centroid":[0.4468,-0.00635,0.04017],"force_p95":0.06847,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10219,"mean_force":0.04489,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44679,-0.02557,0.03784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5166.0,"contact_point_centroid":[0.44666,-0.0448,0.03967],"force_p95":0.06727,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07683,"mean_force":0.04292,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4468,-0.02557,0.03785]}],"total_contact_groups":10},"final_pose_error":0.01116,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.62864,0.20486,0.11821],"final_tcp_position":[0.6243,0.20481,0.14825],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":0.47231,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2204.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.45823,-0.02405,0.13272],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.45426,-0.02584,0.04505],"tcp_start":[0.45823,-0.02405,0.13272],"tcp_to_object_dist_end":0.01952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45847,-0.02571,0.02577],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.3033,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.13872,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11794.0,"raw_peak_contact_force":0.19212,"subtask_id":"grasp_1","tcp_end":[0.44677,-0.02557,0.03782],"tcp_start":[0.45426,-0.02584,0.04505],"tcp_to_object_dist_end":0.0168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60897,0.17188,0.14088],"object_pos_start":[0.45847,-0.02571,0.02577],"object_to_goal_dist_end":0.04984,"object_to_goal_dist_start":0.3033,"object_z_max":0.15062,"peak_contact_force":0.11043,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":33117.0,"raw_peak_contact_force":0.47231,"subtask_id":"transport_arc","tcp_end":[0.59889,0.1717,0.16314],"tcp_start":[0.44677,-0.02557,0.03782],"tcp_to_object_dist_end":0.02443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":18.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.62864,0.20486,0.11821],"object_pos_start":[0.60897,0.17188,0.14088],"object_to_goal_dist_end":0.0055,"object_to_goal_dist_start":0.04984,"object_z_max":0.14088,"peak_contact_force":0.15256,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":23308.0,"raw_peak_contact_force":0.32917,"subtask_id":"release_1","tcp_end":[0.6243,0.20481,0.14825],"tcp_start":[0.59889,0.1717,0.16314],"tcp_to_object_dist_end":0.03035,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19545,"average_solve_count":220.0,"average_success_count":220.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.06572,"approach.speed":0.08201,"descend.grasp_z_offset":0.01,"descend.speed":0.04526,"place_descend.place_speed":0.05124,"place_descend.placement_z_offset":0.02921,"transport.arc_height":0.06159,"transport.placement_z_offset":0.0253,"transport.transport_speed":0.0107},"optimized_scores":{"best_composite_score":0.43383,"best_fitness_score":0.97383,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":86.0,"contact_point_centroid":[0.54009,0.00078,-0.0014],"force_p95":0.51689,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54996,"mean_force":0.17964,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52841,0.00085,0.03466]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18110.0,"contact_point_centroid":[0.56179,0.02756,0.14268],"force_p95":0.08095,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30888,"mean_force":0.05637,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56041,0.04657,0.14088]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17665.0,"contact_point_centroid":[0.56037,0.06381,0.13979],"force_p95":0.08596,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29488,"mean_force":0.0576,"phase_index":3.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55904,0.04475,0.13784]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":13393.0,"contact_point_centroid":[0.63858,0.12828,0.20658],"force_p95":0.09454,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20658,"mean_force":0.06791,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63557,0.1472,0.20592]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":15202.0,"contact_point_centroid":[0.6389,0.16601,0.20644],"force_p95":0.08231,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19644,"mean_force":0.06009,"phase_index":4.0,"phase_name":"place_descend","phase_type":"descend","tcp_position_centroid":[0.63559,0.14722,0.20593]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.5443,0.00101,-0.00203],"force_p95":0.13233,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.15567,"mean_force":0.12541,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53075,0.00088,0.03502]},{"body_a":"world","body_b":"grasp_target","contact_count":2644.0,"contact_point_centroid":[0.54431,0.00113,-0.00194],"force_p95":0.12957,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12281,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51739,0.00049,0.20024]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53638,0.00099,0.07285]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4114.0,"contact_point_centroid":[0.53064,-0.01834,0.03627],"force_p95":0.07621,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11907,"mean_force":0.0518,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52951,0.00086,0.03359]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4879.0,"contact_point_centroid":[0.53057,0.01994,0.03539],"force_p95":0.06827,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09018,"mean_force":0.04473,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52951,0.00086,0.03359]}],"total_contact_groups":10},"final_pose_error":0.01089,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.64908,0.15605,0.18664],"final_tcp_position":[0.64343,0.15627,0.21042],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":0.54996,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2644.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_1","tcp_end":[0.53717,0.001,0.10245],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":800.0,"raw_peak_contact_force":0.12263,"subtask_id":"descend_1","tcp_end":[0.53806,0.00102,0.04364],"tcp_start":[0.53717,0.001,0.10245],"tcp_to_object_dist_end":0.01869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54419,0.00075,0.02587],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25051,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.13041,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.15567,"subtask_id":"grasp_1","tcp_end":[0.52948,0.00086,0.03355],"tcp_start":[0.53806,0.00102,0.04364],"tcp_to_object_dist_end":0.01659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":30.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.63879,0.13676,0.19056],"object_pos_start":[0.54419,0.00075,0.02587],"object_to_goal_dist_end":0.02308,"object_to_goal_dist_start":0.25051,"object_z_max":0.19058,"peak_contact_force":0.08851,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":35861.0,"raw_peak_contact_force":0.54996,"subtask_id":"transport_arc","tcp_end":[0.62911,0.13673,0.20818],"tcp_start":[0.52948,0.00086,0.03355],"tcp_to_object_dist_end":0.0201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.64908,0.15605,0.18664],"object_pos_start":[0.63879,0.13676,0.19056],"object_to_goal_dist_end":0.00512,"object_to_goal_dist_start":0.02308,"object_z_max":0.19056,"peak_contact_force":0.1086,"phase_name":"place_descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28595.0,"raw_peak_contact_force":0.20658,"subtask_id":"release_1","tcp_end":[0.64343,0.15627,0.21042],"tcp_start":[0.62911,0.13673,0.20818],"tcp_to_object_dist_end":0.02445,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```